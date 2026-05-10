def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources we can reach at least as fast; then smaller myd; then larger lead margin.
        if myd <= opd:
            key = (0, myd, -(opd - myd), rx, ry)
        else:
            key = (1, (myd - opd), myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    best_move = [0, 0]
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = man(nx, ny, tx, ty)
        opd_now = man(ox, oy, tx, ty)

        # Blocking pressure: if we can arrive no later than opponent, prioritize that.
        can_win = 1 if myd2 <= opd_now else 0

        # Also avoid moves that bring us closer but would still be losing; prefer moves that maximize chance.
        # Secondary: minimize our distance; tertiary: maximize distance between agents (deterministic crowding avoidance).
        agent_sep = man(nx, ny, ox, oy)
        key = (0 if can_win else 1, -can_win, myd2, -agent_sep)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move