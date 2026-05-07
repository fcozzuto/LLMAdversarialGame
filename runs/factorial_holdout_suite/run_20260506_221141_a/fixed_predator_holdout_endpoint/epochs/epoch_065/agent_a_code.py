def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))

    if not resources:
        return [0, 0]
    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Prefer resources where we are closer AND opponent is farther; break ties by closeness and then position.
    best = None
    best_key = None
    for rx, ry in resources:
        self_d = cheb((sx, sy), (rx, ry))
        opp_d = cheb((ox, oy), (rx, ry))
        steal = opp_d - self_d
        # Small bias: move toward our "half" (lower-sum quadrant from our start) to stay away from deniers.
        side_bias = (rx + ry) - (sx + sy)
        # Reward being strictly closer; penalize if opponent is already closer.
        closer_reward = (opp_d - self_d) * 2 + (1 if self_d < opp_d else -1 if self_d > opp_d else 0)
        key = (closer_reward, steal, -self_d, side_bias, -((rx * 997 + ry * 313) % 1000), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            self_to_target = cheb((nx, ny), (tx, ty))
            opp_to_target = cheb((ox, oy), (tx, ty))
            # Prefer moves that reduce our distance to target; if tied, prefer increasing opponent disadvantage.
            candidates.append((self_to_target, -(opp_to_target - self_to_target), dx, dy))
    # Deterministic pick: smallest distance, then smallest dx/dy ordering by constructed tuple.
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]