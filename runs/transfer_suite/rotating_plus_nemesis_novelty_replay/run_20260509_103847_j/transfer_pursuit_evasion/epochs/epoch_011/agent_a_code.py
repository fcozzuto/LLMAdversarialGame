def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def sgn(a): return 0 if a == 0 else (1 if a > 0 else -1)
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy

    # opponent tends to evade: choose its move to maximize distance; slight preference to corners to avoid being trapped
    vx, vy = sgn(ox - sx), sgn(oy - sy)
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    corner_score = {c: 1 for c in corners}

    def opp_policy(px, py, myx, myy):
        best = None
        for odx, ody in deltas:
            nx, ny = px + odx, py + ody
            if not inb(nx, ny):
                continue
            d = dist2(nx, ny, myx, myy)
            # encourage corner-approach deterministically
            cpen = 0
            if (nx, ny) in corner_score:
                cpen = -w*h
            # also discourage stepping "toward" us
            away = odx * vx + ody * vy
            key = (d, away, -cpen)
            if best is None or key > best[0]:
                best = (key, nx, ny)
        if best is None:
            return px, py
        return best[1], best[2]

    best_move = (0, 0)
    best_key = None
    # prefer capture immediately; otherwise minimize distance against predicted opponent response
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            return [dx, dy]
        px, py = opp_policy(ox, oy, nx, ny)
        d_after = dist2(nx, ny, px, py)

        # additional heuristic: avoid letting opponent cross obstacles by controlling its direction vector
        # prefer moves that reduce its intended direction component
        my_to_opp_dx, my_to_opp_dy = sgn(px - nx), sgn(py - ny)
        ctrl = -(my_to_opp_dx * (dx) + my_to_opp_dy * (dy))

        # corner evasion mitigation: prefer occupying cells that are closer to the corner the opponent is nearest to
        # (computed deterministically)
        best_corner = min(corners, key=lambda c: dist2(px, py, c[0], c[1]))
        corner_dist = dist2(nx, ny, best_corner[0], best_corner[1])

        key = (-d_after, ctrl, -corner_dist)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]