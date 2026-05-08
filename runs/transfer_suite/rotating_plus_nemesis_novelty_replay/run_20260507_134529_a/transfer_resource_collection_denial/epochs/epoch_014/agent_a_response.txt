def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Resource desirability from a given agent position: beat opponent first if possible,
    # otherwise reduce the distance advantage opponent currently has.
    def res_value(px, py, rx, ry):
        myd = man(px, py, rx, ry)
        opd = man(ox, oy, rx, ry)
        if myd <= opd:
            return 100000 - myd  # higher is better; prefer closer wins
        # Otherwise: minimize losing gap; prefer getting closer overall
        return -((myd - opd) * 1000 + myd)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Look one step ahead: evaluate the best resource we could pursue next.
        # Also lightly encourage not moving away from opponent to avoid getting denied indefinitely.
        best_res = None
        for rx, ry in resources:
            v = res_value(nx, ny, rx, ry)
            if best_res is None or v > best_res[0]:
                best_res = (v, rx, ry)
        v, rx, ry = best_res

        myd_next = man(nx, ny, rx, ry)
        oppd_next = man(ox, oy, rx, ry)
        opp_dist = man(nx, ny, ox, oy)

        # Deterministic tie-breaks
        key = (-v, myd_next, -oppd_next, opp_dist, rx, ry, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]