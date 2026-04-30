def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Default: move toward opponent to potentially contest center
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach sooner, and that opponent is far from.
            # Tie-break toward higher y then x deterministically.
            key = (ds, -do, -ry, -rx)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Greedy step: choose move that gets closer to target while avoiding obstacles.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nt = dist((nx, ny), (tx, ty))
        # Secondary: avoid moving into squares that are very close to opponent (contest).
        no = dist((nx, ny), (ox, oy))
        candidates.append((nt, -no, dy, dx, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][3]), int(candidates[0][2])]