def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or role == "pursuer"

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))
        elif isinstance(p, dict) and "position" in p and p["position"]:
            q = p["position"]
            if q and len(q) >= 2:
                res.append((int(q[0]), int(q[1])))

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_op = manh(nx, ny, ox, oy)
        d_best_res = 0
        if res:
            d_best_res = min(manh(nx, ny, rx, ry) for (rx, ry) in res)
        # Primary: chase/avoid opponent; Secondary: chase resources when pursuer, avoid when evader
        val = (-d_op if pursuer else d_op) + ((-d_best_res) if pursuer else (d_best_res) * 0.1)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]