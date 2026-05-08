def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry):
            continue
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        diff = opp_d - our_d  # >0 means we are closer
        # Prefer resources we are closer to; then quicker; then bigger advantage; then stable tiebreak
        key = (0 if diff > 0 else 1, our_d, -diff, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_m = [0, 0]
    best_m_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_next = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        advantage_next = opp_d - our_next

        # Primary: reach quickly (closer to target)
        # Secondary: keep/increase advantage vs opponent
        # Tertiary: avoid moving onto cells that are obstacles (already filtered) and keep within bounds
        key = (our_next, 0 if advantage_next > 0 else 1, -advantage_next, abs(nx - tx) + abs(ny - ty))
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = [dx, dy]

    return best_m