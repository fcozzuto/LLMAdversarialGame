def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    res_set = set(tuple(p) for p in resources)

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target: pick resource where we are relatively closer; break ties by closer-to-us, then lexicographic.
    if resources:
        best = None
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            advantage = opd - myd  # positive => we are closer
            key = (-(advantage), myd, rx, ry)  # minimize for determinism; more advantage => smaller -adv
            if best is None or key < best:
                best = key
                tx, ty = rx, ry
    else:
        tx, ty = ox, oy

    # Penalize states where opponent can capture a resource next turn.
    opp_captures = 0
    for dxo, dyo in moves:
        nxo, nyo = ox + dxo, oy + dyo
        if inb(nxo, nyo) and (nxo, nyo) not in obstacles and (nxo, nyo) in res_set:
            opp_captures = 1
            break

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Main objective: improve closeness to target vs opponent.
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv = opd - myd

        # Big reward for stepping onto a resource.
        pick_bonus = 40 if (nx, ny) in res_set else 0

        # Secondary: reduce opponent immediate capture chances by moving to contested resources.
        block_bonus = 0
        if opp_captures:
            # If we move onto a resource that opponent could take next, that helps; approximate by checking if any opp next move reaches that resource.
            if resources:
                for rx, ry in resources:
                    if (rx, ry) == (nx, ny):
                        for dxo, dyo in moves:
                            nxo, nyo = ox + dxo, oy + dyo
                            if inb(nxo, nyo) and (nxo, nyo) not in obstacles and (nxo, nyo) == (rx, ry):
                                block_bonus = 20
                                break
                        break

        # Tie-break deterministically with lexicographic dx,dy.
        # Higher adv and pick_bonus preferred; also avoid too much drifting from target.
        key = (-(adv + pick_bonus + block_bonus), myd, abs(nx - sx) + abs(ny - sy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move