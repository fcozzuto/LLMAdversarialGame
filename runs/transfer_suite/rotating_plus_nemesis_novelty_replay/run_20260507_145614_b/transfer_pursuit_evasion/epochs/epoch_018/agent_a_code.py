def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    self_role = (observation.get("self_role") or "").lower()
    evader = "evader" in self_role or "escape" in self_role
    if not evader and "pursuer" in self_role:
        evader = False

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append([dx, dy])
    if not moves:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Deterministic tie-break: prefer (0,0), then diagonals? We'll rank by abs(dx)+abs(dy), then dx,dy.
    def key(m):
        dx, dy = m[0], m[1]
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, ox, oy)
        # Evader wants larger distance; pursuer wants smaller.
        score = d if evader else -d
        return (score, -(abs(dx) + abs(dy)), dx, dy)

    return max(moves, key=key)