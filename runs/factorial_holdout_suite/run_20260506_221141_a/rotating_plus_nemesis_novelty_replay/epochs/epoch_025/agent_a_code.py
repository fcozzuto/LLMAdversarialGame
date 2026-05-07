def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - b) + abs(c - d)

    # Strategy shift: parity-aware "arrival race" against opponent's nearest-resources.
    # Prefer resources where we can arrive not later than opponent, with parity advantage,
    # then use tie-break to minimize our distance.
    def rscore(rx, ry):
        my_d = manh(sx, rx, sy, ry)
        opp_d = manh(ox, rx, oy, ry)
        parity_adv = (my_d % 2) - (opp_d % 2)  # smaller is better for us
        lead = opp_d - my_d
        # If we are behind, heavily discount; also prefer higher-distance resources
        # to reduce opponent "last step" stealing.
        if my_d > opp_d:
            return (-10**6 + lead, parity_adv, my_d)
        return (lead, parity_adv, my_d)

    target = min(sorted(resources, key=lambda t: (t[0], t[1])), key=lambda t: rscore(t[0], t[1]))
    tx, ty = target

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_next = manh(nx, tx, ny, ty)
        opp_next = manh(ox, tx, oy, ty)
        # Move that brings us closer; if we are already not leading, reduce opponent's distance less.
        # Parity-first tie-break to preserve arrival timing.
        parity_key = (my_next % 2) - (opp_next % 2)
        lead_key = opp_next - my_next
        key = (-lead_key, parity_key, my_next, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best