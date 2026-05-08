def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v, d=0):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        return d, d

    sx, sy = pos(observation.get("self_position", [0, 0]))
    ox, oy = pos(observation.get("opponent_position", [0, 0]))
    role = observation.get("self_role", "")
    obstacles = set()
    for o in observation.get("obstacles") or []:
        try:
            if isinstance(o, (list, tuple)) and len(o) >= 2:
                x, y = int(o[0]), int(o[1])
            elif isinstance(o, dict) and "x" in o and "y" in o:
                x, y = int(o["x"]), int(o["y"])
            else:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    pursuer_dx = sign(ox - sx)
    pursuer_dy = sign(oy - sy)

    # Project where the evader likely goes (zigzag -> roughly alternating away from pursuer)
    proj_ox = max(0, min(w - 1, ox + (-pursuer_dx)))
    proj_oy = max(0, min(h - 1, oy + (-pursuer_dy)))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return (dx if dx >= 0 else -dx) if (abs(dx) > abs(dy)) else (dy if dy >= 0 else -dy)

    if role == "evader":
        # Run away from projected pursuer position (mirror chase direction).
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # pursuer likely moves toward evader, so evader should maximize distance to projected pursuer
            proj_sx = max(0, min(w - 1, sx + sign(ox - sx)))
            proj_sy = max(0, min(h - 1, sy + sign(oy - sy)))
            score = cheb(nx, ny, proj_sx, proj_sy)
            if best is None or score > best[0]:
                best = (score, [dx, dy])
        return best[1] if best else [0, 0]

    # Pursuer: minimize distance to projected evader.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        score = cheb(nx, ny, proj_ox, proj_oy)
        # Tie-break: prefer moves that also reduce current distance
        score2 = cheb(nx, ny, ox, oy)
        key = (score, score2)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1] if best else [0, 0]