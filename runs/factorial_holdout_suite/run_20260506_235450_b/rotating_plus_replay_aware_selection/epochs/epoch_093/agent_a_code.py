def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_set.add((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy, nx, ny in legal:
        # Immediate collection bonus
        if (nx, ny) in res_set:
            val = 10_000
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
            continue

        best_resource_val = None
        self_adv_sum = 0  # small secondary preference toward overall resources
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            self_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            # Positive means we arrive earlier than opponent; strongly prefer winning resources.
            # Add slight preference for being closer among equally contested resources.
            adv = (opp_d - self_d) - 0.02 * self_d
            if best_resource_val is None or adv > best_resource_val:
                best_resource_val = adv
            self_adv_sum += adv

        # Combine: primary = best contested resource, secondary = encourage moving toward overall advantage.
        val = best_resource_val if best_resource_val is not None else -10_000
        val += 0.001 * self_adv_sum

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

        # Deterministic tiebreak: prefer smallest dx, then dy magnitude toward 0, then lexicographically
        elif val == best_val:
            cand = (dx, dy)
            cur = best_move
            if abs(cand[0]) < abs(cur[0]) or (abs(cand[0]) == abs(cur[0]) and (abs(cand[1]) < abs(cur[1]) or (abs(cand[1]) == abs(cur[1]) and cand < cur))):
                best_move = cand

    return [int(best_move[0]), int(best_move[1])]