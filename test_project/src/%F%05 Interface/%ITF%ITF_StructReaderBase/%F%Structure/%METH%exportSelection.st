{
  "link_always": false, 
  "external": false, 
  "exclude_from_build": false, 
  "enable_system_call": false
}
!__DECLARATION__!
//This method returns the buffer position and size of the currently selected struct/object
METHOD exportSelection : BOOL
VAR_OUTPUT
	position		:POINTER TO EASCII;
	size			:DWORD;
END_VAR
!__IMPLEMENTATION__!
