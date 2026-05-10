def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    evader = ("evader" in role) or ("runner" in role) or ("evade" in role)  # deterministic role inference

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    sxpar = (sx + sy) & 1
    best = None
    best_key = None

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d2 = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)
        parity = ((nx + ny) & 1)

        if not evader:
            # Pursuer: hard minimize distance; tie-break by manhattan, then parity to avoid oscillations.
            # Small additional bias to "keep pressure" by preferring moves that align with the vector to opponent.
            vx, vy = ox - sx, oy - sy
            ax, ay = nx - sx, ny - sy
            align = vx * ax + vy * ay  # larger is better
            key = (d2, man, -align, abs(parity - sxpar))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        else:
            # Evader: maximize distance; tie-break by manhattan, then change parity if possible to reduce capture patterns.
            vx, vy = ox - sx, oy - sy
            ax, ay = nx - sx, ny - sy
            avoid = -(vx * ax + vy * ay)  # larger means moving away more in the chase direction
            key = (-d2, -man, -avoid, abs(parity - sxpar))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)

    return [int(best[0]), int(best[1])]