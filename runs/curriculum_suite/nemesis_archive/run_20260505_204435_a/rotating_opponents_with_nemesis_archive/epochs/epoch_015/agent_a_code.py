def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not targets:
        return [0, 0]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Opportunistic switcher:
        # prefer resources where we are already winning (d_s < d_o),
        # otherwise move to reduce (d_s - d_o) toward opponent.
        win_gain = -10**9
        min_gap = 10**9
        closest_opp = 10**9
        for rx, ry in targets:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < do:
                # maximize closeness among resources we can beat
                win_gain = max(win_gain, (do - ds) * 10 - ds)
            gap = ds - do
            if gap < min_gap:
                min_gap = gap
            # also keep an eye on opponent contest pressure
            closest_opp = min(closest_opp, do)

        # primary: winning move; if none, secondary: reduce our deficit to contest;
        # tertiary: avoid making it too easy for opponent to reach something soon.
        if win_gain > -10**8:
            key = (0, -win_gain, min_gap, closest_opp, dx, dy)
        else:
            key = (1, min_gap, closest_opp, man(nx, ny, ox, oy), dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]