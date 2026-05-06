def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def man(nx, ny, tx, ty):
        return abs(tx - nx) + abs(ty - ny)

    def target_value(tx, ty):
        d_me = man(x, y, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        lead = d_opp - d_me
        return lead * 1000 - d_me + 0.01 * d_opp

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best = None
    best_tv = None
    for tx, ty in resources:
        tv = target_value(tx, ty)
        if best is None or tv > best_tv or (tv == best_tv and (tx, ty) < best):
            best = (tx, ty)
            best_tv = tv
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_before = man(x, y, tx, ty)
        d_after = man(nx, ny, tx, ty)
        opp_d_after = man(ox, oy, tx, ty)  # opponent move assumed unknown
        # Prefer reducing distance to target; break ties by improving relative advantage.
        rel_before = man(ox, oy, tx, ty) - d_before
        rel_after = man(ox, oy, tx, ty) - d_after
        penalty = 0
        # Softly avoid moving away from both axes toward the target.
        penalty += 0.1 * (abs((nx - tx)) + abs((ny - ty)))
        moves.append((-(d_after - d_before), rel_after - rel_before, -d_after, -opp_d_after, -penalty, dx, dy))
    moves.sort()
    if moves:
        return [moves[0][-2], moves[0][-1]]

    return [0, 0]