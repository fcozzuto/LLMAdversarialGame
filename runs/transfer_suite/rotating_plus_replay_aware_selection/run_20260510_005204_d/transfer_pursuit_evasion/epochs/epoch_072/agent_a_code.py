def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)
    we_pursuer = not we_evader

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_prox_pen(x, y):
        # Penalize being on/adjacent to obstacles to avoid getting trapped.
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xi, yj = x + dx, y + dy
                if (xi, yj) in blocked:
                    p += 3 if dx == 0 and dy == 0 else 1
        return p

    best_move = [0, 0]
    best_score = None

    # Deterministic tie-break order: prefer earlier in this list.
    moves = [
        (0, 0), (-1, -1), (0, -1), (1, -1),
        (-1, 0), (1, 0),
        (-1, 1), (0, 1), (1, 1)
    ]

    cur_d = cheb(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Obstacles block movement in this environment (if engine prevents, staying is handled).
        # We still evaluate; heavy penalty discourages landing on obstacles.
        if (nx, ny) in blocked:
            continue

        nd = cheb(nx, ny, ox, oy)
        delta = nd - cur_d
        # If evader: maximize distance, if pursuer: minimize distance.
        main = delta if we_evader else -delta
        score = main * 100 - obst_prox_pen(nx, ny) * 5

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Fallback: if all moves invalid due to obstacles, stay.
    return best_move