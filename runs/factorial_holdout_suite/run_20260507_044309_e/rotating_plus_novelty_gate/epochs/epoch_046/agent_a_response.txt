def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    resources = observation.get("resources", []) or []
    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: (md(m[2], m[3], tx, ty), valid.index(m)))
        return [best[0], best[1]]

    res = [tuple(r) for r in resources]

    opp_idx = min(range(len(res)), key=lambda i: (md(ox, oy, res[i][0], res[i][1]), i))
    opp_t = res[opp_idx]

    def best_move_toward(tx, ty):
        return min(valid, key=lambda m: (md(m[2], m[3], tx, ty), valid.index(m)))

    our_d_opp_t = md(sx, sy, opp_t[0], opp_t[1])
    opp_d_opp_t = md(ox, oy, opp_t[0], opp_t[1])

    # If we can contest the opponent's nearest target (reach no later), go there.
    if our_d_opp_t <= opp_d_opp_t:
        m = best_move_toward(opp_t[0], opp_t[1])
        return [m[0], m[1]]

    # Otherwise, pick a resource where we are likely to arrive earlier than the opponent.
    best_m = None
    best_key = None
    for i in range(len(res)):
        rx, ry = res[i]
        d_ours = md(sx, sy, rx, ry)
        d_opps = md(ox, oy, rx, ry)
        margin = d_opps - d_ours  # positive if we are closer/earlier
        # Prefer: earlier than opponent, then closer, then deterministic tie by index.
        key = (-1 if margin > 0 else 1, -margin if margin > 0 else margin, d_ours, i)
        if best_key is None or key < best_key:
            best_key = key
            best_m = (rx, ry)

    m = best_move_toward(best_m[0], best_m[1])
    return [m[0], m[1]]