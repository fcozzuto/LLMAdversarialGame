def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def local_options(x, y):
        c = 0
        for adx, ady in moves:
            nx, ny = x + adx, y + ady
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    best_move = (0, 0)
    best_val = None

    # deterministic tie-break: fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d = dist2(nx, ny, ox, oy)
        opt = local_options(nx, ny)
        center = dist2(nx, ny, cx, cy) * 0.001

        # pursuer: minimize distance; evader: maximize distance.
        # also prefer moves that keep more local mobility and avoid hugging obstacles.
        if is_evader:
            val = d - 0.35 * (8 - opt) - center
        else:
            val = -d + 0.25 * opt - center

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]