def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Targeting shift: choose moves that maximize "advantage" to the best resource
    # while also reducing opponent reach (interference).
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not ok(nx, ny):
            continue

        if resources:
            my_d = min(dist((nx, ny), r) for r in resources)
            opp_d = min(dist((ox, oy), r) for r in resources)
            # Evaluate against each resource: prefer those closer to us and farther from opponent
            val = 0
            for r in resources:
                d_us = dist((nx, ny), r)
                d_opp = dist((ox, oy), r)
                # If opponent is already very close, deprioritize; otherwise, "steal" by moving closer.
                val += (d_opp - d_us) * 7 - d_us * 2
                # Extra weight for near-term capture
                if d_us == 0:
                    val += 10**6
                elif d_us == 1:
                    val += 2500
                # Penalize moving into opponent proximity to avoid giving race advantage
                d_to_opp = dist((nx, ny), (ox, oy))
                if d_to_opp <= 1:
                    val -= 60
                elif d_to_opp <= 2:
                    val -= 18
            # Also incorporate overall proximity balance
            val += (opp_d - my_d) * 5
        else:
            # No resources visible: move to a corner-adjacent "control" point away from opponent.
            # Deterministically steer toward the farthest corner with obstacle avoidance.
            corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
            best_corner = max(corners, key=lambda c: dist((ox, oy), c))
            val = -dist((nx, ny), best_corner) - dist((nx, ny), (ox, oy)) * 2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]