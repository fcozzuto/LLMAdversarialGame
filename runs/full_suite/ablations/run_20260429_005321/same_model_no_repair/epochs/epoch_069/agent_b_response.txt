def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}
    t = observation.get("turn_index", 0)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def near_obst(x, y):
        if (x, y) in obst: return 10**6
        p = 0
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)):
            if (nx, ny) in obst: p += 3
        return p

    # Choose target deterministically by advantage: opponent farther than self => better
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if (rx, ry) in obst: continue
            # Prefer resources self can reach sooner than opponent; break ties toward closer-to-opponent-far
            key = (do - ds, -(ds), -near_obst(rx, ry), -(abs(rx-(w-1)/2)+abs(ry-(h-1)/2)), rx, ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        # No resources: head toward center-ish with obstacle penalty
        tx, ty = (w - 1)//2, (h - 1)//2

    # Greedy one-step move toward target with obstacle and tie-break
    best_move = (0, 0)
    best_val = None
    # Deterministic tie-break pattern with turn parity
    order = moves if (t % 2 == 0) else moves[::-1]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            val = -10**9
        else:
            d_to = cheb(nx, ny, tx, ty)
            d_now = cheb(sx, sy, tx, ty)
            # Also slightly discourage moving near obstacles
            val = (d_now - d_to) * 1000 - d_to - near_obst(nx, ny)
            # If we can capture soon (adjacent), prefer moves that keep parity stable
            if d_to == 0: val += 10**7
            if d_to == 1: val += 1000
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    # Ensure integers in allowed set
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]