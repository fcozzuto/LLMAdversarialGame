def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs.add((px, py))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                rlist.append((rx, ry))
    if not rlist:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Choose target deterministically by maximizing a value; penalize moves where opponent can arrive sooner.
        move_val = -10**9
        for rx, ry in rlist:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Prefer resources we can reach no later than opponent, strongly.
            # Tie-break via closer to us and farther from opponent; slight preference for staying closer overall.
            val = 1000 * (do - ds) + (-2 * ds) + (1 * (do)) + (-0.1 * md(nx, ny, sx, sy))
            if val > move_val:
                move_val = val

        # If currently standing on a resource, stay is best (handled naturally since ds=0 gives big score).
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]