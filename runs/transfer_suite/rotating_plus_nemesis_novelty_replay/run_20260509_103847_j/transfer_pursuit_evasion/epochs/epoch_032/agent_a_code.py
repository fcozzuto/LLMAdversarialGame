def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    role = str(observation.get("self_role", "pursuer")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        if (x, y) in obstacles:
            return 10**9
        # Repel from obstacles and discourage moving adjacent when possible
        p = 0
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 10**9
            if d == 1:
                p += 7
            elif d == 2:
                p += 2
        return p

    # Determine desired direction: chase directly, but if blocked, bias around nearest obstacle
    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        oc = obstacle_penalty(nx, ny)

        # Wall-run bias: prefer moves that keep same relative ordering to opponent along dominant axis
        # (i.e., align x or y first to "slide" around obstacles deterministically).
        sx_to_ox = ox - sx
        sy_to_oy = oy - sy
        nx_to_ox = ox - nx
        ny_to_oy = oy - ny
        align = 0
        if abs(sx_to_ox) >= abs(sy_to_oy):
            # align x more than y
            align = -abs(nx_to_ox) + abs(sx_to_ox)
        else:
            align = -abs(ny_to_oy) + abs(sy_to_oy)

        # Small center preference for evader to avoid immediate corner trapping by pursuer
        center_pref = 0
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pref = dist2(nx, ny, int(cx), int(cy)) * 0.01

        # Objective
        if is_evader:
            score = -d - 0.5 * oc + 0.25 * align + 0.1 * center_pref
        else:
            # Strongly minimize distance; break ties by obstacle penalty and alignment
            score = d + 0.6 * oc - 0.25 * align + 0.1 * center_pref

        if best_score is None or (score < best_score if not is_evader else score > best_score):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]