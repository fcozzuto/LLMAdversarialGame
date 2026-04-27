def choose_move(observation):
    turn_index = observation.get('turn_index', 0)
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    remaining = observation.get('remaining_resource_count', len(resources))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y):
        return 0 <= x < w and 0 <= y < h
    def free(x,y):
        return inb(x,y) and (x,y) not in obstacles and not (x==ox and y==oy)
    def dist(a,b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If there are resources, bias toward closer ones while considering opponent
    best_move = (0,0)
    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            ds = dist((sx,sy),(rx,ry))
            do = dist((ox,oy),(rx,ry))
            key = (do - ds, -ds)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx,ry)
        rx, ry = best_r
        # choose a move that approaches the selected resource while avoiding opponent and obstacles
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # simple heuristic: prefer reducing distance to resource and not getting closer to opponent
            nds = dist((nx,ny),(rx,ry))
            ndo = dist((nx,ny),(ox,oy))
            val = ( -nds, -ndo )
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # If no resources, move to maximize distance from opponent while staying in bounds and avoiding obstacles
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dopp = dist((nx,ny),(ox,oy))
        val = ( -dopp )
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]