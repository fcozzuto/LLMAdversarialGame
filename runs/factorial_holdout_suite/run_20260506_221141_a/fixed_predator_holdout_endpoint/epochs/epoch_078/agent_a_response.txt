def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h:
            resources.append((x, y))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        for dx, dy in [(1, 1), (1, 0), (0, 1), (0, 0), (1, -1), (-1, 1), (-1, 0), (0, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    remaining = int(observation.get("remaining_resource_count") or len(resources))
    collect_weight = 1.0 + (12 - min(12, remaining)) * 0.08

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Prioritize a resource where we gain time/priority over the opponent.
        # "Denier" behavior: prefer states where (opp_dist - self_dist) is large.
        best_resource_gain = -10**18
        best_self_dist = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            gain = (od - sd) * (1.5 if od > sd else 1.0)
            # As resources dwindle, strongly prefer closer reachable resources.
            val = gain + collect_weight * (-0.08 * sd)
            if val > best_resource_gain or (val == best_resource_gain and sd < best_self_dist):
                best_resource_gain = val
                best_self_dist = sd

        # Add a small tiebreak: don't drift too slowly when we can be the leader.
        center_bias = -0.002 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        val_move = best_resource_gain + center_bias + (-0.01 * best_self_dist if best_resource_gain > 0 else 0.01 * best_self_dist)
        if val_move > best_val:
            best_val = val_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]