/**
 * @license Copyright (c) 2003-2023, CKSource Holding sp. z o.o. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	config.toolbarGroups = [
		{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
		{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
		{ name: 'styles', groups: [ 'styles' ] },
		{ name: 'forms', groups: [ 'forms' ] },
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'colors', groups: [ 'colors' ] },
		{ name: 'paragraph', groups: [ 'align', 'list', 'indent', 'blocks', 'bidi', 'paragraph' ] },
		{ name: 'links', groups: [ 'links' ] },
		{ name: 'insert', groups: [ 'insert' ] },
		{ name: 'tools', groups: [ 'tools' ] },
		{ name: 'others', groups: [ 'others' ] }
	];

	config.removeButtons = 'TextColor,BGColor,Save,NewPage,Print,Preview,Templates,Cut,Copy,Paste,HiddenField,ImageButton,Button,Select,Textarea,TextField,Radio,Checkbox,Form,Smiley,SelectAll,CreateDiv,Language,BidiRtl,BidiLtr,Iframe,PageBreak,Flash,About,Maximize,ShowBlocks,Source,Anchor,SpecialChar,Table,Font,Superscript,Subscript,Replace,Find,Scayt,CopyFormatting,PasteText,PasteFromWord,Styles,FontSize';
	config.skin = "index_theme";
	config.height= 450;
	config.removePlugins = 'resize,image';
	config.extraPlugins = 'image2,embed,autoembed,autolink,textmatch';
	config.language = "uk";
	config.embed_provider = '//ckeditor.iframe.ly/api/oembed?url={url}&callback={callback}&api_key=bf3242c812a699ed249972';
};
