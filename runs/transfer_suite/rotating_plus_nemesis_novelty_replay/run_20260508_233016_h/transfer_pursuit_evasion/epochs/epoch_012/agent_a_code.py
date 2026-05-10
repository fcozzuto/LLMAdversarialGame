def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" not in self_role and "purs" in opp_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def obst_penalty(x, y):
        if (x, y) in blocked:
            return 10_000
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in blocked:
                    pen += 3
        return pen

    best_move = [0, 0]
    best_val = None

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue

        d = dist(nx, ny, ox, oy)
        c = abs(nx - center_x) + abs(ny - center_y)
        # wall-runner tends to hug/escape around obstacles; staying away helps pursuer,
        # while evader tries to keep distance while not colliding.
        p = obst_penalty(nx, ny)
        val = d if pursuer else -d
        val += (1 if pursuer else -1) * 0.02 * c
        val += (0.4 if pursuer else 0.2) * p

        if best_val is None or (val < best_val if pursuer else val > best_val):
            best_val = val
            best_move = [dx, dy]

    # Fallback: if all moves blocked, try any in-bounds move (engine will keep in place if invalid).
    if best_val is None:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]

    return best_move