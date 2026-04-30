def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    x, y = self_pos
    ox, oy = opp_pos

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(nx, ny):
        nx = nx if nx >= 0 else 0
        ny = ny if ny >= 0 else 0
        nx = nx if nx < w else w - 1
        ny = ny if ny < h else h - 1
        return nx, ny

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) + abs(dy)

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        nx, ny = clamp(nx, ny)
        if (nx, ny) in obstacles:
            continue

        # Prefer moves that improve relative access to resources (contest)
        best_contest = None
        best_self_d = None
        for r in resources:
            r = (r[0], r[1])
            if r in obstacles:
                continue
            sd = dist((nx, ny), r)
            od = dist((ox, oy), r)
            # Lower is better; strongly reward becoming closer than opponent
            contest = sd - od
            if best_contest is None or contest < best_contest or (contest == best_contest and sd < best_self_d):
                best_contest = contest
                best_self_d = sd

        # If no resources, drift toward center deterministically
        if best_contest is None:
            score = -dist((nx, ny), (w // 2, h // 2))
        else:
            # Encourage getting closer overall, and minimize distance if already favorable
            score = (-best_contest * 10) - best_self_d

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]