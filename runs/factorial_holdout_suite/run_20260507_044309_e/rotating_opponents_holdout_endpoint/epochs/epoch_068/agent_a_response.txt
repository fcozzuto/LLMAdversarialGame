def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for diagonal moves

    # Score resources by advantage over opponent, then prefer closer to self, then deterministic ordering.
    scored = []
    for x, y in resources:
        sdi = dist((sx, sy), (x, y))
        odi = dist((ox, oy), (x, y))
        advantage = odi - sdi
        # If opponent is at/near the resource, still compete but de-prioritize.
        score = (advantage * 1000) + (-sdi * 10) + (-((x + y) % 7))
        scored.append((score, x, y, sdi, odi))
    scored.sort(reverse=True)
    _, tx, ty, _, _ = scored[0]

    # Choose among legal deltas by reducing distance to target, avoiding obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        curd = dist((sx, sy), (tx, ty))
        # Prefer moves that decrease distance; slight preference for also being ahead of opponent on that move.
        nAdv = dist((ox, oy), (tx, ty)) - nd
        step_score = (curd - nd) * 10000 + nAdv * 50 - (dx == 0 and dy == 0) * 5
        # Deterministic tiebreak
        step_score -= (nx * 131 + ny * 17) % 13
        if best is None or step_score > best[0]:
            best = (step_score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]