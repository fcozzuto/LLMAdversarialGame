def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_dx, best_dy = 0, 0
    best_val = -10**18
    opp_rel = abs(sx - ox) + abs(sy - oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Strong preference: resources where we are closer than opponent (oppd-selfd large).
        # Secondary: keep moving toward good targets (lower self distance), and avoid letting opponent get closer.
        val = -3 * (abs(nx - ox) + abs(ny - oy))  # general safety: don't drift toward opponent
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            adv = oppd - selfd  # positive means we out-approach now
            # If opponent is closer (adv < 0), still take it if it's the least losing and selfd is small.
            sc = adv * 7 - selfd * 1
            # Bonus for winning by a margin; discourages chasing hopelessly denied resources.
            if adv > 1:
                sc += 10
            else:
                sc -= (1 - adv) * 2
            # Tiny deterministic tiebreaker based on position parity.
            sc += ((rx + ry + nx + ny) & 1) * 0.01
            if sc > val:
                val = sc

        # Encourage choosing a move that also increases our relative advantage.
        val += (abs(ox - sx) + abs(oy - sy) - abs(ox - nx) - abs(oy - ny)) * 0.5
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]