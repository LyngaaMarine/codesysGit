{
  "link_always": false, 
  "external": false, 
  "exclude_from_build": false, 
  "enable_system_call": false
}
!__DECLARATION__!
//This adds a value data to the buffer
// |**Version**|**Author**| **Date** |**Changes** 
// | 1         | NSN      | 22-06-20 | Creation
METHOD writeLint
VAR_INPUT
	value			:LINT;
END_VAR
VAR
	buffer			:STRING(20);
END_VAR
!__IMPLEMENTATION__!
IF ready AND (afterKey OR_ELSE inArray OR_ELSE singleVal) THEN
	buffer					:=		TO_STRING(value);
	addString(pString:=ADR(buffer));
	lastComma		:=		bufferPosition;
	addChar(char:=EASCII.Comma);
	IF NOT(useSingleLine) AND NOT(treeSingleLine[treeLevel]) THEN
		addNewLine();
	END_IF
	afterKey		:=		FALSE;
	singleVal		:=		FALSE;
	emptyBlock		:=		FALSE;
END_IF
