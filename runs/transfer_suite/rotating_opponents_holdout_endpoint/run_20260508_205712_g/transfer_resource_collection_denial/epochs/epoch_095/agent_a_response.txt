def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = sorted(deltas, key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Evaluate how strongly this next position can out-race opponent on the best remaining resource.
        best_for_next = -10**18
        for rx, ry in resources:
            st = cheb(nx, ny, rx, ry)
            ot = cheb(ox, oy, rx, ry)
            # Primary: maximize advantage (opponent takes longer).
            # Secondary: minimize our time (finish sooner).
            # Tertiary: prefer moves that are closer to resources on the way.
            adv = ot - st
            val = (adv * 1000) - st
            if (rx, ry) == (sx, sy):
                val += 500000  # already on a resource (unlikely, but strong)
            if val > best_for_next:
                best_for_next = val
        if best_for_next > best_val:
            best_val = best_for_next
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]