def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_adj = {(ox + dx, oy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)}

    best_move = (0, 0)
    best_val = -10**18
    # Strategic change vs pure chase: race-to-best-resource with danger penalty for stepping near opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obs:
            continue

        danger = 1 if (nx, ny) in opp_adj else 0
        # choose target resource that maximizes a deterministic score from this candidate position
        local_best = -10**18
        my_pos = (nx, ny)
        my_d_now = min(dist(my_pos, r) for r in resources)
        # small bias to reduce my distance overall while denying opponent access
        for r in resources:
            sd = dist(my_pos, r)
            od = dist((ox, oy), r)
            # primary: win the race to that resource, then prefer closer-to-me, then safer
            val = (od - sd) * 1000 - sd * 2 + (my_d_now == sd) * 3 - danger * 20
            # break ties by preferring resources "towards my corner" deterministically
            val += -0.001 * (sd + abs(r[0] - 0) + abs(r[1] - 0))
            if val > local_best:
                local_best = val
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]