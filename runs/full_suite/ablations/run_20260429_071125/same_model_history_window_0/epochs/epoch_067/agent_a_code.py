def choose_move(observation):
    grid_w = observation.get('grid_width', 8)
    grid_h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    if not resources:
        deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        best = (-(10**9), 0, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if nx < 0 or nx >= grid_w or ny < 0 or ny >= grid_h: 
                continue
            if (nx, ny) in obstacles:
                continue
            dopp = max(abs(nx-ox), abs(ny-oy))
            score = d2 = -dopp
            cand = (score, abs(nx-ox)+abs(ny-oy), dx, dy)
            if cand > best:
                best = cand
        return [best[2], best[3]] if best[3] or best[2] else [0, 0]

    def dist(a, b, c, d):
        return max(abs(a-c), abs(b-d))

    # Pick a resource where we are relatively closest to gain score advantage.
    best_res = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Primary: opponent minus self (larger => we are closer)
        # Secondary: smaller self distance
        val = (do - ds, -ds)
        if best_val is None or val > best_val:
            best_val = val
            best_res = (rx, ry)
    if best_res is None:
        best_res = resources[0]

    tx, ty = best_res
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx+dx, sy+dy
        if nx < 0 or nx >= grid_w or ny < 0 or ny >= grid_h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds_next = dist(nx, ny, tx, ty)
        do_next = dist(ox, oy, tx, ty)
        # Encourage staying competitive while approaching target
        score = (do_next - ds_next, -ds_next, -dist(nx, ny, ox, oy))
        cand = (score, -abs(dx) - abs(dy), dx, dy)
        if best is None or cand > best:
            best = cand
    if best is None:
        return [0, 0]
    return [best[2], best[3]]