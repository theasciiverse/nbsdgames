/*
Asciiverse: show each game centred in the terminal.

The games draw on stdscr at fixed positions from the top left corner. Here
stdscr is swapped for a pad as soon as curses starts, so every drawing call
in the games works unchanged; refresh() then shows the part of the pad the
game has drawn on, centred in the terminal.

The centred area is that of the current screen: while what is drawn keeps
overlapping it (a board being played, a message coming and going), it only
grows, so the picture does not jump about; when the game moves to another
screen (from a question to the board, from the board to its help page), the
area starts over. Mouse positions are translated back to the game's own
coordinates, and a resized terminal re-centres the picture (the game never
sees KEY_RESIZE). A terminal too small for the game shows its top left
part, as before.

Released into the public domain under CC0, like the rest of New BSD Games.
*/
#ifndef CENTRE_H
#define CENTRE_H

#define NB_PAD_LINES 100
#define NB_PAD_COLS 300

static WINDOW* nb_pad;//where the game draws
static chtype* nb_row;//one row of it, for measuring
static int nb_top,nb_left,nb_bottom=-1,nb_right=-1;//the current screen's area, inclusive
static int nb_oy,nb_ox,nb_lines,nb_cols;//where that is shown, for which terminal size
//a game whose world runs past its field sets these to the field's size
static int nb_max_lines=NB_PAD_LINES,nb_max_cols=NB_PAD_COLS;

static WINDOW* nb_initscr(void){
	if(!nb_pad){
		initscr();
		nb_pad=newpad(LINES>NB_PAD_LINES?LINES:NB_PAD_LINES,COLS>NB_PAD_COLS?COLS:NB_PAD_COLS);
		nb_row=nb_pad?malloc((getmaxx(nb_pad)+1)*sizeof(chtype)):NULL;
		if(nb_pad && nb_row){
			stdscr=nb_pad;
		}
		else if(nb_pad){//no memory: draw at the top left as before
			delwin(nb_pad);
			nb_pad=NULL;
		}
	}
	return stdscr;
}

//the area of every cell that is not a plain blank; false when there is none
static bool nb_measure(int* top,int* left,int* bottom,int* right){
	int h=getmaxy(nb_pad),w=getmaxx(nb_pad);
	if(h>nb_max_lines)h=nb_max_lines;
	if(w>nb_max_cols)w=nb_max_cols;
	*top=h;*left=w;*bottom=-1;*right=-1;
	for(int y=0;y<h;++y){
		int n=mvwinchnstr(nb_pad,y,0,nb_row,w);
		for(int x=0;x<n;++x){
			if(nb_row[x]!=(chtype)' '){
				if(y<*top)*top=y;
				if(y>*bottom)*bottom=y;
				if(x<*left)*left=x;
				if(x>*right)*right=x;
			}
		}
	}
	return *bottom>=0;
}

//keep the current screen's area, grown, or start a new one
static void nb_follow(int top,int left,int bottom,int right){
	if(nb_bottom>=0){
		int it=top>nb_top?top:nb_top,ib=bottom<nb_bottom?bottom:nb_bottom;
		int il=left>nb_left?left:nb_left,ir=right<nb_right?right:nb_right;
		long both=(it<=ib && il<=ir)?(long)(ib-it+1)*(ir-il+1):0;
		long drawn=(long)(bottom-top+1)*(right-left+1);
		long area=(long)(nb_bottom-nb_top+1)*(nb_right-nb_left+1);
		if(2*both>=drawn+area-both){//overlapping by half or more: the same screen
			if(top<nb_top)nb_top=top;
			if(left<nb_left)nb_left=left;
			if(bottom>nb_bottom)nb_bottom=bottom;
			if(right>nb_right)nb_right=right;
			return;
		}
	}
	nb_top=top;nb_left=left;nb_bottom=bottom;nb_right=right;
}

static int nb_refresh(void){
	if(!nb_pad){
		return wrefresh(stdscr);
	}
	int cy,cx,top,left,bottom,right;
	getyx(nb_pad,cy,cx);
	bool drawn=nb_measure(&top,&left,&bottom,&right);
	wmove(nb_pad,cy,cx);
	if(drawn){
		nb_follow(top,left,bottom,right);
	}
	if(nb_bottom<0){//nothing drawn yet
		stdscr=nb_pad;
		return OK;
	}
	int h=nb_bottom-nb_top+1,w=nb_right-nb_left+1;
	int oy=LINES>h?(LINES-h)/2:0;
	int ox=COLS>w?(COLS-w)/2:0;
	if(oy!=nb_oy || ox!=nb_ox || LINES!=nb_lines || COLS!=nb_cols){
		//the picture moved: blank the old place
		WINDOW* screen=newwin(0,0,0,0);
		if(screen){
			wnoutrefresh(screen);
			delwin(screen);
		}
		nb_oy=oy;nb_ox=ox;nb_lines=LINES;nb_cols=COLS;
	}
	int vh=h<LINES?h:LINES,vw=w<COLS?w:COLS;
	pnoutrefresh(nb_pad,nb_top,nb_left,oy,ox,oy+vh-1,ox+vw-1);
	int r=doupdate();
	stdscr=nb_pad;//ncurses points stdscr back at the screen in doupdate
	return r;
}

static int nb_getch(void){
	if(!nb_pad){
		return wgetch(stdscr);
	}
	nb_refresh();//wgetch does not refresh a pad by itself
	int c;
	while((c=wgetch(nb_pad))==KEY_RESIZE){
#ifdef PDCURSES
		resize_term(0,0);
#endif
		stdscr=nb_pad;
		nb_refresh();
	}
	stdscr=nb_pad;
	return c;
}

#ifndef NO_MOUSE
//mouse positions come in terminal coordinates; the game wants its own
static int nb_mouse_to_game(MEVENT* e){
	e->y+=nb_top-nb_oy;
	e->x+=nb_left-nb_ox;
	return OK;
}
#ifdef PDCURSES
static int nb_nc_getmouse(MEVENT* e){
	int r=nc_getmouse(e);
	if(r==OK)nb_mouse_to_game(e);
	return r;
}
#define nc_getmouse(e) nb_nc_getmouse(e)
#else
static int nb_getmouse(MEVENT* e){
	int r=getmouse(e);
	if(r==OK)nb_mouse_to_game(e);
	return r;
}
#define getmouse(e) nb_getmouse(e)
#endif
#endif //NO_MOUSE

#undef initscr
#define initscr() nb_initscr()
#undef refresh
#define refresh() nb_refresh()
#undef getch
#define getch() nb_getch()

#endif //CENTRE_H
