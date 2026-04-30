def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        # Manhattan (fast, deterministic); diagonals still allowed so use Chebyshev for movement realism
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue

        if resources:
            best = -10**9
            for rx, ry in resources:
                myd = dist((nx, ny), (rx, ry))
                opd = dist((ox, oy), (rx, ry))
                # Prefer becoming closer than opponent; also prefer resources nearer overall
                score = (opd - myd) * 10 - myd
                # Small bias to reduce distance to opponent (interception/block)
                score += max(0, 3 - dist((nx, ny), (ox, oy)))
                best = score if score > best else best
            # If we can land on a resource, boost strongly
            if (nx, ny) in set(map(tuple, resources)):
                best += 1000
        else:
            # No resources: head toward center
            cx, cy = (w - 1) // 2, (h - 1) // 2
            best = -dist((nx, ny), (cx, cy))

        candidates.append((best, nx - sx, ny - sy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]