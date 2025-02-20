{
  "link_always": false, 
  "external": false, 
  "exclude_from_build": false, 
  "enable_system_call": false
}
!__DECLARATION__!
//This adds a string of text to the JSON buffer
//Illigal characters { , } , " they will be skipped
// |**Version**|**Author**| **Date** |**Changes**
// | 1         | NSN      | 22-06-20 | Creation
METHOD PROTECTED addStringRaw
VAR_INPUT
	pString			:POINTER TO BYTE;	//Address of string for the comment text
END_VAR
!__IMPLEMENTATION__!
IF ready THEN		//It only runs when a buffer has been initialized
	IF pString <> 0 THEN						//Checks if stringaddress is not empty
		WHILE pString^ <> EASCII.Null DO			//Runs until null is detected
			IF bufferPosition < bufferMaxADR THEN	//In normal conditions
				bufferPosition^		:=		pString^;	
				pString				:=		pString + 1;
				bufferPosition		:=		bufferPosition + 1;
			ELSE
				bufferInvalid		:=		TRUE;	
				EXIT;
			END_IF
		END_WHILE
	END_IF
END_IF
