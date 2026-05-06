def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    # Assume opponent goes for its nearest resource; deny that target.
    opp_target = min(resources, key=lambda r: md(ox, oy, r[0], r[1]))
    tx, ty = opp_target

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_own_to_target = md(nx, ny, tx, ty)
        d_opp_to_target = md(ox, oy, tx, ty)
        # Main objective: get to/maintain advantage on opponent's target.
        deny = (d_opp_to_target - d_own_to_target) * 10

        # Secondary: also improve ability to take any resource quickly.
        d_to_closest = min(md(nx, ny, r[0], r[1]) for r in resources)
        pickup = -d_to_closest

        # Tertiary: avoid stepping away from opponent (to keep pressure vs "shadow").
        approach = -md(nx, ny, ox, oy)

        # Blocking bonus: if we can get adjacent to the target, prioritize.
        block = 0
        if md(nx, ny, tx, ty) == 1:
            block = 25
        elif md(nx, ny, tx, ty) == 0:
            block = 60

        score = deny + pickup + approach + block

        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: lexicographic (dx, dy)
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return best_move