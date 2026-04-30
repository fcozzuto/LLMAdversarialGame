def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    seen = set()
    for p in resources:
        if p and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs and t not in seen:
                seen.add(t); res.append(t)

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not res:
        best = (0, 0); bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                d = cheb(nx, ny, ox, oy)
                if d > bestv:
                    bestv = d; best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0); best_val = -10**18
    move_set = set(res)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_on = (nx, ny) in move_set
        my_d_opp = cheb(nx, ny, ox, oy)
        best_for_this = -10**18
        for rx, ry in res:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can claim earlier (or equal), otherwise reduce opponent leverage.
            earlier = 1 if md <= od else 0
            val = 0
            val += 200000 if my_on and (nx, ny) == (rx, ry) else 0
            val += earlier * 6000
            val += (1500 - md * 120) if earlier else (800 - od * 90 - md * 10)
            # Small tie-break: keep moves that also keep us away from opponent (reduce contest).
            val += (my_d_opp * 3)
            # Also slightly diversify by preferring not-too-distant resources overall.
            val += - (md * md)
            if val > best_for_this:
                best_for_this = val
        if best_for_this > best_val:
            best_val = best_for_this; best_move = (dx, dy)

    return [best_move[0], best_move[1]]