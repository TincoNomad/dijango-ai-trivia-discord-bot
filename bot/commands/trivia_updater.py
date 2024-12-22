from discord import Message, Client, DMChannel
from ..api_client import TriviaAPIClient
from ..utils.logging_bot import command_logger
from typing import Dict, Any, List, Optional

class TriviaUpdater:
    def __init__(self, client: Client):
        self.client = client
        self.api_client = TriviaAPIClient()
        
    async def handle_list_trivias(self, message: Message) -> Optional[List[Dict[str, Any]]]:
        """Handles listing trivias for a user through DM"""
        try:
            username = message.author.name
            command_logger.info(f"Listing trivias for user: {username}")
            
            # Send initial message to original channel
            await message.channel.send("I've sent you a DM to show you all trivias available!")
            
            params: Dict[str, str] = {"username": username}
            trivias: List[Dict[str, Any]] = await self.api_client.get_user_trivias(params)
            
            if not trivias:
                await message.author.send("You don't have any trivias created yet.")
                return None
                
            trivia_list = "\n".join(
                f"{i+1}. {trivia['title']} - Difficulty: {trivia['difficulty']} - Theme: {trivia['theme']}"
                for i, trivia in enumerate(trivias)
            )
            
            await message.author.send(f"Your trivias:\n```\n{trivia_list}\n```")
            return trivias
            
        except Exception as e:
            command_logger.error(f"Error listing trivias: {e}")
            await message.author.send("Error getting the list of trivias.")
            return None
            
    async def ask_continue_update(self, message: Message, is_error: bool = False) -> bool:
        """Asks user if they want to continue updating and handles the response"""
        question = "Would you like to try updating something else? (yes/no)" if is_error else "Would you like to update something else? (yes/no)"
        await message.author.send(question)
        
        def check_continue(m):
            return (
                m.author == message.author and 
                isinstance(m.channel, DMChannel) and
                m.content.lower() in ['yes', 'no']
            )
        
        try:
            response = await self.client.wait_for('message', timeout=30.0, check=check_continue)
            if response.content.lower() == 'yes':
                return True
            else:
                await message.author.send("✅ Update process completed!")
                return False
        except TimeoutError:
            await message.author.send("⏰ No response received. Update process completed!")
            return False

    async def handle_update_trivia(self, message: Message) -> None:
        """Handles updating a trivia through DM"""
        try:
            trivias = await self.handle_list_trivias(message)
            if not trivias:
                return
            
            # Select trivia
            await message.author.send("Which trivia would you like to update? (Enter the number)")
            
            def check(m):
                return (
                    m.author == message.author and 
                    isinstance(m.channel, DMChannel) and 
                    m.content.isdigit() and 
                    1 <= int(m.content) <= len(trivias)
                )
                
            response = await self.client.wait_for('message', timeout=30.0, check=check)
            trivia_index = int(response.content) - 1
            selected_trivia = trivias[trivia_index]
            command_logger.info(f"Selected trivia for update: {selected_trivia['title']}")
            
            # Show update options
            await message.author.send(
                "What would you like to update?\n"
                "1. Title\n"
                "2. Difficulty (1-5)\n"
                "3. Theme\n"
                "4. Questions and Answers"
            )
            
            def check_option(m):
                return (
                    m.author == message.author and 
                    isinstance(m.channel, DMChannel) and 
                    m.content in ['1', '2', '3', '4']
                )
            
            response = await self.client.wait_for('message', timeout=30.0, check=check_option)
            field_choice = int(response.content)
            
            # Handle basic fields
            field_mapping = {
                1: "title",
                2: "difficulty",
                3: "theme"
            }
            
            await message.author.send("Enter the new value:")
            
            def check_value(m):
                return m.author == message.author and isinstance(m.channel, DMChannel)
            
            response = await self.client.wait_for('message', timeout=60.0, check=check_value)
            new_value = response.content
            command_logger.info(f"New value received: {new_value}")
            
            # Validar si el nuevo valor es igual al actual
            current_value = selected_trivia[field_mapping[field_choice]]
            command_logger.info(f"Current value: {current_value}")
            
            if str(new_value).lower() == str(current_value).lower():
                command_logger.info("Update cancelled: new value is same as current")
                await message.author.send("❗ The new value is the same as the current value. No update needed.")
                
                if await self.ask_continue_update(message):
                    return await self.handle_update_trivia(message)
                return
            
            # Validar el título antes de actualizar
            if field_choice == 1:
                while True:  # Bucle para permitir múltiples intentos
                    existing_trivias = await self.api_client.get_user_trivias({"username": message.author.name})
                    existing_titles = [t['title'] for t in existing_trivias if t['id'] != selected_trivia['id']]
                    command_logger.info(f"Existing titles: {existing_titles}")
                    
                    if new_value in existing_titles:
                        command_logger.info(f"Update cancelled: title '{new_value}' already exists")
                        await message.author.send("❌ That title already exists. Please enter a different title:")
                        
                        try:
                            response = await self.client.wait_for('message', timeout=60.0, check=check_value)
                            new_value = response.content
                            command_logger.info(f"New title attempt received: {new_value}")
                        except TimeoutError:
                            await message.author.send("⏰ Time's up! Update cancelled.")
                            if await self.ask_continue_update(message):
                                return await self.handle_update_trivia(message)
                            return
                    else:
                        break  # Título válido, continuar con la actualización
            
            update_data = {
                field_mapping[field_choice]: int(new_value) if field_choice == 2 else new_value
            }
            command_logger.info(f"Preparing to update trivia {selected_trivia['id']} with data: {update_data}")
            
            # Send update to API
            try:
                await self.api_client.patch_trivia(
                    selected_trivia["id"], 
                    update_data,
                    username=message.author.name
                )
                command_logger.info(f"Successfully updated trivia {selected_trivia['id']}")
                await message.author.send("✅ Trivia updated successfully!")
                
                if await self.ask_continue_update(message):
                    return await self.handle_update_trivia(message)
                return
                
            except Exception as e:
                command_logger.error(f"Error updating trivia {selected_trivia['id']}: {str(e)}")
                await message.author.send("❌ Error updating the trivia. Please try again.")
                
                if await self.ask_continue_update(message, is_error=True):
                    return await self.handle_update_trivia(message)
                return
            
        except TimeoutError:
            await message.author.send("⏰ Time's up! Please try again.")
        except Exception as e:
            command_logger.error(f"Error updating trivia: {e}")
            await message.author.send("❌ Error updating the trivia.")