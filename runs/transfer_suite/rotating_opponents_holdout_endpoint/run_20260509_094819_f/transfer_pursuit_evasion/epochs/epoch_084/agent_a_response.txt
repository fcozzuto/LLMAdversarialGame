def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = observation.get("self_role", "") or ""
    role_lower = self_role.lower()
    pursuer = ("purs" in role_lower) or (role_lower == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_score = None
    best_move = [0, 0]

    # Deterministic tie-break order: earliest in moves list
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        d = cheb(nx, ny, ox, oy)
        # Capture if exact overlap (radius 0)
        capture_bonus = 0
        if d == 0:
            capture_bonus = 100000 if pursuer else -100000

        # Also gently avoid stepping into immediate obstacle "tight" spots by counting blocked neighbors
        adj_blocked = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in blocked:
                adj_blocked += 1

        if pursuer:
            # Minimize distance; prioritize capture, then distance, then fewer adjacent blocked
            score = -d * 100 - adj_blocked + capture_bonus
        else:
            # Evader: maximize distance; prioritize staying away, then fewer adjacent blocked
            score = d * 100 - adj_blocked + capture_bonus

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked, stay put
    return best_move