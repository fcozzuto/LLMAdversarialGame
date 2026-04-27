def choose_move(observation):
    w=observation.get("grid_width",8); h=observation.get("grid_height",8)
    sp=observation["self_position"]; op=observation["opponent_position"]
    rx=observation.get("resources",[]); ox=observation.get("obstacles",[])
    obstacles=set((p[0],p[1]) for p in ox)
    def clamp(v,lo,hi):
        return lo if v<lo else hi if v>hi else v
    def cheb(a,b):
        dx= a[0]-b[0]; dy=a[1]-b[1]
        return (dx if dx>=0 else -dx) if (abs(dx)>=abs(dy)) else (dy if dy>=0 else -dy)
    deltas=[(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move=(0,0); best_score=-10**18
    for dx,dy in deltas:
        nx=sp[0]+dx; ny=sp[1]+dy
        if nx<0 or nx>=w or ny<0 or ny>=h or (nx,ny) in obstacles:
            nx,ny=sp[0],sp[1]
        me=(nx,ny)
        opp=tuple(op)
        s=0
        for r in rx:
            rt=(r[0],r[1])
            d1=cheb(me,rt); d2=cheb(opp,rt)
            adv=d2-d1
            if adv>=0:
                s += 20/(d1+1) + 60 if d1==0 else 0
            else:
                s += adv/(d2+1)  # still progress if we can't secure
        s -= 0.8*cheb(me,opp)
        if s>best_score or (s==best_score and (dx,dy)<best_move):
            best_score=s; best_move=(dx,dy)
    return [int(best_move[0]), int(best_move[1])]