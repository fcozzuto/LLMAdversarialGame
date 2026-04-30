def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx*dx + dy*dy) ** 0.5
    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y
    if not resources:
        # No resources known: drift away from opponent, but avoid obstacles
        best = None
        bestv = 1e18
        for dx, dy in cand:
            nx, ny = clamp(sx+dx, sy+dy)
            if (nx, ny) in obstacles:
                continue
            dopp = dist(nx, ny, ox, oy)
            # maximize distance => minimize negative
            v = -dopp
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))
    # Deterministic target: minimize (self_dist - opp_dist), then self_dist
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        dk = dist(sx, sy, rx, ry) - dist(ox, oy, rx, ry)
        key = (dk, dist(sx, sy, rx, ry), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    rx, ry = best_res
    # Choose move that reduces target distance; also tries to widen advantage vs opponent
    best_move = (0, 0)
    best_val = 1e18
    for dx, dy in cand:
        nx, ny = clamp(sx+dx, sy+dy)
        if (nx, ny) in obstacles:
            continue
        d_self = dist(nx, ny, rx, ry)
        d_opp = dist(ox, oy, rx, ry)
        gap = d_self - d_opp  # smaller is better for us
        d_opp_here = dist(nx, ny, ox, oy)
        # Penalize moving closer to opponent slightly (helps contest indirectly)
        v = (d_self*1.6 + gap*2.2) - (d_opp_here*0.25)
        # Prefer moves that reduce target distance compared to current
        v += (dist(sx, sy, rx, ry) - d_self) * (-1.0)
        if v < best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]