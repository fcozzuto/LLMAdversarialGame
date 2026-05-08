def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick best next step by minimizing: (we lag) then distance; prefer higher advantage.
    best_key = None
    best_move = [0, 0]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        best_selfd = 10**9
        best_adv = -10**9
        best_margin = -10**9
        best_rx = 0
        best_ry = 0

        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - selfd  # positive means we are closer or equal under tie-break race
            # race-first: maximize margin; tie-break by smaller selfd, then deterministic cell id
            if (adv > best_adv) or (adv == best_adv and (selfd < best_selfd or (selfd == best_selfd and (rx, ry) < (best_rx, best_ry)))):
                best_adv = adv
                best_selfd = selfd
                best_margin = adv
                best_rx, best_ry = rx, ry

        # If we can't beat opponent on any resource this turn (margin < 0), still minimize our distance to the "best" resource.
        # Key: we want larger best_adv, but also quick completion and safety.
        lag = 0 if best_margin >= 0 else (-best_margin)
        key = (lag, best_selfd, best_rx + 100 * best_ry, -best_adv, -dx, -dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]