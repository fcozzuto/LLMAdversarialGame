def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role)
    is_pursuer = ("purs" in role) or ("seeker" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs or not in_bounds(x, y)

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx*dx + dy*dy

    best = (None, None, None)  # (score, nx, ny)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if is_evader:
            # Head to farthest corner from pursuer; tie-break by increasing distance.
            tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
            score = dist2(nx, ny, ox, oy)
            # Encourage moving toward chosen corner a bit.
            score += dist2(nx, ny, tx, ty) * -0.01
        else:
            # Pursuer: minimize distance to evader; also try to align diagonally.
            score = -dist2(nx, ny, ox, oy)
            # Small preference for diagonal progress.
            adx = 0 if ox == nx else 1
            ady = 0 if oy == ny else 1
            score += (1 if (abs(ox-nx) and abs(oy-ny)) else 0) * 0.001
        if best[0] is None or score > best[0] or (score == best[0] and (nx, ny) < (best[1], best[2])):
            best = (score, nx, ny)

    if best[0] is None:
        return [0, 0]
    return [best[1] - sx, best[2] - sy]