def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    center = (w // 2, h // 2)
    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # If we're on a resource, prefer staying.
        if (nx, ny) in set(resources):
            return [dx, dy]

        # Score: maximize resource "win" margin (opponent distance - ours), break ties by closeness.
        if resources:
            rkey = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer cells that can reach a resource earlier; also avoid huge detours.
                key = (-(opd - myd), myd, rx, ry)
                if rkey is None or key < rkey:
                    rkey = key
            # Convert to a move key: smaller is better.
            move_key = (rkey[0], rkey[1], abs(nx - center[0]) + abs(ny - center[1]), dx, dy)
        else:
            # No visible resources: move toward center while keeping deterministic preference.
            move_key = (cheb(nx, ny, center[0], center[1]), dx, dy)

        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]