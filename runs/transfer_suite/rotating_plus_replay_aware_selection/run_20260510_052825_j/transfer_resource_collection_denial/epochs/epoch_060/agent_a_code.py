def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    turns_remaining = int(observation.get("turns_remaining", 0))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = []
    for rx, ry in resources:
        if inb(rx, ry) and (rx, ry) not in obstacles:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we arrive earlier; otherwise pick contested-but-close options late game.
        # Small tie-break favors nearer to us to reduce dithering.
        time_pressure = 1 if turns_remaining <= 8 else 0
        advantage = od - sd
        score = (-(1 if advantage > 0 else 0), -advantage, sd - od * time_pressure, sd, rx, ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Greedy on getting closer to target; also avoid moves that would give opponent a better immediate claim.
        contested = cheb(ox, oy, tx, ty) - nds
        mscore = (nds, -contested, abs(dx) + abs(dy), nx, ny)
        if best_m is None or mscore < best_m[0]:
            best_m = (mscore, [dx, dy])

    if best_m is None:
        return [0, 0]
    return best_m[1]