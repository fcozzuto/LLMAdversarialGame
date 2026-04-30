def choose_move(observation):
    w=observation['grid_width']; h=observation['grid_height']
    sx,sy=observation['self_position']; ox,oy=observation['opponent_position']
    obstacles=set((x,y) for x,y in observation.get('obstacles',[]))
    resources=observation.get('resources',[])
    if not resources:
        # Move toward opponent to contest space
        dx=(1 if ox>sx else -1 if ox<sx else 0)
        dy=(1 if oy>sy else -1 if oy<sy else 0)
        nx,ny=sx+dx,sy+dy
        if 0<=nx<w and 0<=ny<h and (nx,ny) not in obstacles:
            return [dx,dy]
        for ddx in (-1,0,1):
            for ddy in (-1,0,1):
                if ddx==0 and ddy==0: 
                    continue
                nx,ny=sx+ddx,sy+ddy
                if 0<=nx<w and 0<=ny<h and (nx,ny) not in obstacles:
                    return [ddx,ddy]
        return [0,0]

    def cheb(a,b,c,d):
        da=c-a; db=d-b
        return abs(da) if abs(da)>abs(db) else abs(db)

    moves=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move=(0,0); best_val=-10**9

    # Precompute "near obstacles" penalty for a cell
    # (local only via simple neighbor check)
    def obstacle_penalty(x,y):
        p=0
        for ddx in (-1,0,1):
            for ddy in (-1,0,1):
                if ddx==0 and ddy==0: 
                    continue
                if (x+ddx,y+ddy) in obstacles:
                    p+=1
        return p

    for ddx,ddy in moves:
        nx,ny=sx+ddx,sy+ddy
        if not (0<=nx<w and 0<=ny<h): 
            continue
        if (nx,ny) in obstacles:
            continue

        # If standing on a resource, prioritize strongly
        standing_on = 1 if (nx,ny) in set(tuple(r) for r in resources) else 0

        # Choose resource that maximizes our advantage
        # score: prefer smaller self distance; prefer larger opponent distance gap
        val=standing_on*1000
        for rx,ry in resources:
            ds=cheb(nx,ny,rx,ry)
            do=cheb(ox,oy,rx,ry)
            # advantage: positive if we are closer or equal
            adv=(do-ds)
            # also encourage going to closer resource overall
            val=max(val, standing_on*1000 + adv*50 - ds - obstacle_penalty(nx,ny)*2)

        # Secondary: avoid getting too close to obstacles in general already in val; tie-break toward opponent's farthest
        if val>best_val:
            best_val=val; best_move=(ddx,ddy)

    return [int(best_move[0]), int(best_move[1])]