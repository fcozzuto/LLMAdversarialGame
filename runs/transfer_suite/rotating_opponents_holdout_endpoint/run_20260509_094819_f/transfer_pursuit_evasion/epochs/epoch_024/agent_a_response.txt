def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        # Evader: maximize distance; Pursuer: minimize distance
        primary = dist if is_evader else -dist
        # Obstacle-aware: prefer moves that don't step into "tight" spots
        local_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if not (0 <= xx < w and 0 <= yy < h) or (xx, yy) in blocked:
                    local_block += 1
        # Smaller local_block is better for pursuer; larger is better for evader (more escape space)
        secondary = -local_block if is_evader else local_block
        # Deterministic tie-break: prefer diagonal/forward-ish moves toward maximizing corner bias
        corner_bias = (nx + ny * 0.01) if (ox + oy) >= (w - 1) else ((w - 1 - nx) + (h - 1 - ny) * 0.01)
        candidates.append((primary, secondary, corner_bias, dx, dy))

    if not candidates:
        return [0, 0]

    # Sort with deterministic direction depending on role
    candidates.sort(reverse=True)
    best = candidates[0]
    return [int(best[3]), int(best[4])]