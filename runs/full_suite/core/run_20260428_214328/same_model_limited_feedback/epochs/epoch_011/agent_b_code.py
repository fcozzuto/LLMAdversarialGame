def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Best resource from a given position; tie-break deterministically by x,y
    def best_resource(pos):
        if not resources:
            return None
        px, py = pos
        best = None
        best_key = None
        for rx, ry in resources:
            d = dist((px, py), (rx, ry))
            key = (d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    # Fallback target: center-ish
    center = (w//2, h//2)

    target_from_self = best_resource((sx, sy)) or center
    target_from_opp = best_resource((ox, oy)) or center

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose the most beneficial resource for the resulting position
        t = best_resource((nx, ny))
        if t is None:
            t = center

        my_d = dist((nx, ny), t)
        opp_d = dist((ox, oy), t)

        # If opponent is closer, bias toward disrupting by moving toward that same contested target
        # and away from the opponent's nearest target when not already going for resources.
        opp_target_dist = dist((nx, ny), target_from_opp)

        # Strongly prefer being on a resource
        on_res = 1 if (nx, ny) in resources else 0

        # Heuristic: minimize my distance, maximize distance advantage over opponent, and slightly prefer reducing opp_target_dist
        score = (on_res * 1000) + (opp_d - my_d) * 10 - my_d - (opp_target_dist * 0.05)

        # Deterministic tie-break: lexicographically smaller move among equals
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If all candidate moves were invalid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]