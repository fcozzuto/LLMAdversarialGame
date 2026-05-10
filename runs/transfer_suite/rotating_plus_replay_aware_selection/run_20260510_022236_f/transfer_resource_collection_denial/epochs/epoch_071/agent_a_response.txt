def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_cell = None
    best_score = None

    # Counter sweep_rows: prioritize resources on rows far from opponent's current y,
    # while still taking those where we are closer than the opponent.
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds  # positive => we are closer
        row_far = abs(ry - oy)
        time_fit = 0
        if tr > 0:
            # favor quicker grabs without wasting too much time
            time_fit = 2 if ds <= tr else (-1 if ds <= tr + 2 else -3)
        score = advantage * 5 + row_far * 2 + time_fit
        key = (score, -ds, row_far, -cheb(ox, oy, rx, ry))
        if best_score is None or key > best_score:
            best_score = key
            best_cell = (rx, ry)

    if best_cell is None:
        return [0, 0]

    rx, ry = best_cell
    # Choose among legal moves the one that decreases cheb distance most, with
    # slight tie-break toward increasing row separation from opponent.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None
    cur_d = cheb(sx, sy, rx, ry)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = cheb(nx, ny, rx, ry)
        improve = nd - cur_d
        row_sep = abs(ny - oy)
        key = (-improve, nd, row_sep, dx == 0 and dy == 0)
        # deterministic: higher key wins via tuple comparison after negation above
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]