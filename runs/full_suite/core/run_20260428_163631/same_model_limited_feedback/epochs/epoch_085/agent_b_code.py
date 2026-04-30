def choose_move(observation):
    w=observation["grid_width"]; h=observation["grid_height"]
    sx,sy=observation["self_position"]; ox,oy=observation["opponent_position"]
    resources=observation["resources"]; obstacles=set(tuple(p) for p in observation["obstacles"])
    if not resources:
        # fallback: move away from opponent slightly
        dx=0 if ox==sx else (1 if ox<sx else -1)
        dy=0 if oy==sy else (1 if oy<sy else -1)
        return [dx,dy]
    def dist(a,b):
        return abs(a[0]-b[0])+abs(a[1]-b[1])
    # score resources: prefer those we can reach sooner than opponent
    best=None
    for r in resources:
        rx,ry=r
        ds=dist((sx,sy),(rx,ry))
        do=dist((ox,oy),(rx,ry))
        # higher is better
        val=(do-ds)*10 - ds
        if best is None or val>best[0] or (val==best[0] and ds<best[1]):
            best=(val,ds,(rx,ry))
    tx,ty=best[2]
    candidates=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            nx=sx+dx; ny=sy+dy
            if dx==0 and dy==0:
                pass
            if nx<0 or nx>=w or ny<0 or ny>=h: 
                continue
            if (nx,ny) in obstacles: 
                continue
            ds=dist((nx,ny),(tx,ty))
            # also discourage moving closer to opponent unless it helps take target
            approach=-dist((nx,ny),(ox,oy)) + dist((sx,sy),(ox,oy))
            val=-ds*3 + approach
            # if move lands on another resource, bias strongly
            if (nx,ny) in set(map(tuple,resources)):
                val+=50
            candidates.append((val,dx,dy))
    if not candidates:
        return [0,0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]