def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
        elif isinstance(p, dict) and "x" in p and "y" in p:
            x, y = int(p["x"]), int(p["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    role = str(observation.get("self_role") or observation.get("role") or "").lower()
    evader = "evader" in role

    # Candidate moves (deterministic tie-break order)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        d = cheb(nx, ny, ox, oy)
        score = d if evader else -d

        # Micro-avoidance: prefer staying away from obstacles for evader, closer for pursuer (consistent)
        # (counts blocked neighbors in next position)
        blocked = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if not inb(tx, ty) or (tx, ty) in obs:
                blocked += 1
        score += (blocked * (0.001 if evader else -0.001))

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best