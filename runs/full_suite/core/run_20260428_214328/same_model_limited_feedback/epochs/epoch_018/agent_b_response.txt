def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        # drift toward center deterministically
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 0 if sx == int(tx) else (1 if sx < tx else -1)
        dy = 0 if sy == int(ty) else (1 if sy < ty else -1)
        return [dx, dy]

    # Choose a target resource that we are more likely to reach first
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_self = abs(rx - sx) + abs(ry - sy)
        d_opp = abs(rx - ox) + abs(ry - oy)
        # Prefer closer to us, and penalize resources where opponent is clearly closer
        key = (d_self - 0.6 * d_opp, d_self, -d_opp, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    moves = [[dx, dy] for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Distance to target (Chebyshev-ish due to diagonal moves)
        d1 = max(abs(rx - nx), abs(ry - ny))
        # Also consider stealing-friendly: if opponent could arrive immediately, bias away
        d_opp_next_to_target = max(abs(rx - ox - dx), abs(ry - oy - dy))
        pickup = 1.0 if (nx, ny) in map(tuple, resources) else 0.0

        score = (
            -d1
            + 2.2 * pickup
            - 0.35 * max(0, d_opp_next_to_target - d1)  # slight anti-steal pressure
        )

        if best_score is None or score > best_score + 1e-9:
            best_score = score
            best_move = [dx, dy]
        elif abs(score - best_score) <= 1e-9:
            # Deterministic tie-break: lowest (dy, dx) then move order fixed by moves list
            if moves.index([dx, dy]) < moves.index(best_move):
                best_move = [dx, dy]

    return best_move